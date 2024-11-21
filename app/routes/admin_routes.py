from flask import Blueprint, render_template, redirect, url_for, session, request, flash

from ..services.complaint_service import ComplaintService
from ..services.user_service import UserService, PromoteUserResult

admin_routes = Blueprint("admin_routes", __name__)

def check_admin_session():
    if "user_id" not in session:
        return redirect(url_for("auth_routes.welcome"))

    if not UserService.is_admin(session["user_id"]):
        return redirect(url_for("user_routes.panel"))

    return None

@admin_routes.route("/panel")
def panel():
    redirect_response = check_admin_session()
    if redirect_response:
        return redirect_response

    return render_template("admin_panel.html")


@admin_routes.route("/promote-user", methods=["GET", "POST"])
def promote_user():
    redirect_response = check_admin_session()
    if redirect_response:
        return redirect_response
    message = None
    error_message = None
    if request.method == "POST":
        user_email = request.form["email"]
        res = UserService.promote_user(user_email)
        if res is None:
            message = "Promoted user successfully"
        else:
            error_message = res.value

    return render_template("admin_promote_user.html", message=message, error_message=error_message)


@admin_routes.route("/view-complaints")
def view_complaints():
    redirect_response = check_admin_session()
    if redirect_response:
        return redirect_response
    complaints = ComplaintService.get_unresolved()

    return render_template("admin_view_complaints.html", complaints=complaints)


@admin_routes.route("/complaint/<int:complaint_id>", methods=["POST", "GET"])
def complaint(complaint_id: int):
    redirect_response = check_admin_session()
    if redirect_response:
        return redirect_response
    complaint = ComplaintService.get_id(complaint_id)   

    return render_template("admin_complaint.html", complaint=complaint)

@admin_routes.route("/decline-complaint/<int:complaint_id>")
def decline_complaint(complaint_id: int):
    redirect_response = check_admin_session()
    if redirect_response:
        return redirect_response
    
    return redirect(url_for("admin_routes.view-complaints"))
