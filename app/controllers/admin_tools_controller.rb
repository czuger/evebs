class AdminToolsController < ApplicationController

  def show
    @accounts_counts = User.count

    @user_log = {}
    @user_log_last_days = {}

    UserActivityLog.where.not( user: nil ).each do |ual|

      @user_log[ ual.user ] = 0 unless @user_log[ ual.user ]
      @user_log[ ual.user ] += 1

      @user_log_last_days[ ual.user ] = 0 unless @user_log_last_days[ ual.user ]
      @user_log_last_days[ ual.user ] += 1 if ual.updated_at > Time.now - ( 60*60*7)
    end
  end

end
