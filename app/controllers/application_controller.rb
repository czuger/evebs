class ApplicationController < ActionController::Base
  # Prevent CSRF attacks by raising an exception.
  # For APIs, you may want to use :null_session instead.
  protect_from_forgery with: :exception

  def require_logged_in!
    redirect_to new_sessions_path unless current_user
  end

  def log_client_activity
    ip = request.remote_ip
    action = controller_name + '#' + action_name
    UserActivityLog.create!( ip: ip, action: action )
  end

  private
  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end

  helper_method :current_user

end
