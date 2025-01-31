"""
Routes for admin users
"""
# import flask libraries (Third-party libraries)
from flask import Blueprint, render_template, redirect, url_for, session, request, current_app

# import local python libraries
from python_files.functions.SQLFunctions import *
from python_files.functions.NormalFunctions import *
from python_files.classes.Forms import *

# import python standard libraries
import re
from urllib.parse import quote_plus, unquote_plus

adminBP = Blueprint("adminBP", __name__, static_folder="static", template_folder="template")

@adminBP.route("/admin-profile")
def adminProfile():
    userInfo = sql_operation(table="user", mode="get_user_data", userID=session["admin"])
    adminID = userInfo.uid
    adminUsername = userInfo.username
    adminEmail = userInfo.email

    return render_template("users/admin/admin_profile.html", username=adminUsername, email=adminEmail, adminID=adminID, accType=userInfo.role)

@adminBP.route("/user-management", methods=["GET","POST"])
def userManagement():
    if (session.get("isSuperAdmin")):
        return redirect(url_for("superAdminBP.adminManagement"))

    pageNum = request.args.get("p", default=1, type=int)
    if (pageNum < 1):
        return redirect(
            re.sub(current_app.config["CONSTANTS"].NEGATIVE_PAGE_NUM_REGEX, "p=1", request.url, count=1)
        )

    recoverUserForm = AdminRecoverForm(request.form)
    # Form actions starts below
    if (request.method == "POST"):
        userID = request.form.get("uid", default=None, type=str)
        formType = request.form.get("formType", default=None, type=str)
        if (userID is None or formType is None):
            flash("No account ID or form type was provided upon submission of form.", "Error")
            return redirect(session["relative_url"])

        userInfo = sql_operation(table="user", mode="get_user_data", userID=userID)
        if (userInfo is None):
            flash("No user account was found with the provided ID.", "No Such User!")
            return redirect(session["relative_url"])

        if (userInfo.role == "Admin" or userInfo.role == "SuperAdmin"):
            flash("An error occurred while processing your request.", "Sorry!")
            return redirect(session["relative_url"])

        if (formType == "recoverUser" and not userInfo.googleOAuth):
            if (recoverUserForm.validate()):
                newEmail = recoverUserForm.email.data
                generatedToken = False
                try:
                    # change user's email address to the new one and deactivate the user's account 
                    # to prevent the attacker from changing the email address again
                    token = sql_operation(
                        table="user", mode="recover_account", userID=userID, 
                        email=newEmail, isUserAcc=True, oldUserEmail=userInfo.email
                    )
                    generatedToken = True
                except (SameAsOldEmailError):
                    flash("The new email entered is the same as the old email...", "Error recovering user's account!")
                except (EmailAlreadyInUseError):
                    flash("The new email entered is already in use...", "Error recovering user's account!")
                except (UserAccountIsRecoveringError):
                    flash(
                        Markup("The user's account is already in the process of being recovered.<br>However, if you wish to revoke the recovery process, please do that instead of recovering the user's account again."), 
                        "Recovering User's Account Request Rejected"
                    )

                if (generatedToken):
                    flash(f"The user, {userID}, has its email changed to {newEmail} and the instructions to reset his/her password has bent sent to the new email.", f"User's Account Details Updated!")

                    htmlBody = (
                        "Great news! Your account has been recovered by an administrator on our side.<br>",
                        f"Your account email address has been changed to {newEmail} during the account recovery process.",
                        "However, you still need to reset your password by clicking the link below.<br>",
                        "Please click the link below to reset your password.",
                        f"<a href='{current_app.config['CONSTANTS'].CUSTOM_DOMAIN}{url_for('guestBP.recoverAccount', token=token)}' style='{current_app.config['CONSTANTS'].EMAIL_BUTTON_STYLE}' target='_blank'>Reset Password</a>",
                        "Note: This link will expire in 15 days."
                    )
                    send_email(to=newEmail, subject="Account Recovery", body="<br>".join(htmlBody))
            else:
                flash("The email provided was invalid when recovering the user's account.", "Error recovering user's account!")

        elif (formType == "disableTwoFA" and userInfo.hasTwoFA):
            disabledTwoFA = False
            try:
                sql_operation(table="2fa_token", mode="delete_token_and_backup_codes", userID=userID)
                disabledTwoFA = True
            except (No2FATokenError):
                flash(f"The user, {userID}, does not have two-factor authentication enabled on their account.", "Error disabling 2FA!")

            if (disabledTwoFA):
                htmlBody = (
                    "Great news! An administrator has disabled two-factor authentication on your account.",
                    "Please contact an administrator if you have any questions or if you think this is a mistake."
                )
                send_email(
                    to=userInfo.email, subject="Two-Factor Authentication Disabled", body="<br><br>".join(htmlBody)
                )
                flash(
                    Markup(f"The user, {userID}, has its 2 Factor Authentication <span class='text-danger'>disabled</span>!"), 
                    "Two-Factor Authentication Disabled!"
                )

        elif (formType == "revokeRecoveryProcess" and not userInfo.googleOAuth):
            try:
                sql_operation(table="acc_recovery_token", mode="revoke_token", userID=userID)
                flash(f"The user's account recovery process has been revoked and the account has been reactivated for the user.", "Recovery Process Revoked!")
            except (UserAccountNotRecoveringError):
                flash("The user's account is not in the process of being recovered.", "Error Revoking Recovery Process!")

        elif (formType == "deleteUser"):
            sql_operation(table="user", mode="delete_user_data", userID=userID)
            flash(f"The user, {userID}, has been deleted.", "User Deleted!")

        elif (formType == "changeUsername"):
            newUsername = request.form.get("newUsername", default=None, type=str)
            if (newUsername is None):
                flash("No new username was provided upon submission of form.", "Error")
            else:
                try:
                    sql_operation(table="user", mode="change_username", userID=userID, username=newUsername)
                    flash(f"The user, {userID}, has its username changed to {newUsername}.", "User's Account Details Updated!")
                except (ReusedUsernameError):
                    flash("The new username entered is already in use...", "Error changing user's username!")

        elif (formType == "resetProfileImage" and userInfo.hasProfilePic and "https://storage.googleapis.com/coursefinity" in userInfo.profileImage):
            sql_operation(table="user", mode="delete_profile_picture", userID=userID)
            flash(f"The user, {userID}, has its profile picture reset.", "User's Account Details Updated!")

        elif (formType == "banUser" and userInfo.status != "Banned"):
            sql_operation(table="user", mode="ban_user", userID=userID)
            flash(f"The user, {userID}, has been banned.", "User's Account Details Updated!")

        elif (formType == "unbanUser" and userInfo.status == "Banned"):
            sql_operation(table="user", mode="unban_user", userID=userID)
            flash(f"The user, {userID}, has been unbanned.", "User's Account Details Updated!")

        else:
            flash("An error occurred while processing your request.", "Sorry!")

        return redirect(session["relative_url"])

    userInput = request.args.get("user", default=None, type=str)
    userInput = quote_plus(userInput) if (userInput is not None) else None
    if (userInput is not None):
        filterInput = request.args.get("filter", default="username", type=str)
        if (filterInput not in ("username", "uid", "email")):
            filterInput = "username"

        userInput = userInput[:100] # limit user input to 100 characters to avoid buffer overflow when querying in MySQL
        userArr, maxPage = sql_operation(
            table="user", mode="paginate_users", pageNum=pageNum, 
            userInput=unquote_plus(userInput), filterType=filterInput, role="User"
        )
    else:
        userArr, maxPage = sql_operation(table="user", mode="paginate_users", pageNum=pageNum, role="User")

    if (pageNum > maxPage):
        return redirect(
            re.sub(current_app.config["CONSTANTS"].PAGE_NUM_REGEX, f"p={maxPage}", request.url, count=1)
        )

    # Compute the buttons needed for pagination
    paginationArr = get_pagination_arr(pageNum=pageNum, maxPage=maxPage)

    # save the current URL in the session for when the admin searches and an error occurs
    session["relative_url"] = request.full_path
    return render_template("users/admin/user_management.html", currentPage=pageNum, userArr=userArr, maxPage=maxPage, paginationArr=paginationArr, form=recoverUserForm)