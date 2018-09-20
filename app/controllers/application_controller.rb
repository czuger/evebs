class ApplicationController < ActionController::Base
  # Prevent CSRF attacks by raising an exception.
  # For APIs, you may want to use :null_session instead.
  protect_from_forgery with: :exception

  def require_logged_in!
    redirect_to '/' unless current_user
  end

  def require_admin!
    redirect_to denied_admin_tools_path unless current_user.admin
  end

  def log_client_activity
    # ip = request.remote_ip
    # action = controller_name + '#' + action_name
    # user = current_user.name if current_user
    # UserActivityLog.create!( ip: ip, action: action, user: user )
  end

  def get_jita
    @jita ||= TradeHub.find_by_eve_system_id( 30000142 )
    @jita
  end


  private

  def current_user
    return @current_user if @current_user

    if session[:user_id]
      @current_user = User.where( id: session[:user_id] ).first
    end

    @current_user
  end

  def set_user
    @user = current_user
  end

  helper_method :current_user

end
