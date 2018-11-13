class UsersController < ApplicationController

  before_action :require_logged_in!
  before_action :set_user

  # GET /users/1/edit
  def edit
    set_small_screen
    @title = 'Editing user'
    @user = current_user
  end

  # PATCH/PUT /users/1
  # PATCH/PUT /users/1.json
  def update
    @user = current_user
    respond_to do |format|

      # TODO : replace that with something more secure
      # TODO : never trust full update

      ActiveRecord::Base.transaction do
        # Need to remove all white spaces, because the string is formatted as 9 999 999,99
        params['user']['min_amount_for_advice'].gsub!( ' ', '' ) if params['user']['min_amount_for_advice']

        if @user.update(user_params)
          @user.update_attribute(:last_changes_in_choices,Time.now)

          flash.now[ :notice ] = 'User updated successfully.'
          format.html { redirect_to edit_users_path }
        else
          flash.now[ :alert ] = @user.errors
          format.html { redirect_to edit_users_path }
        end
      end
    end
  end

  def update_user_sales_orders_margin_filter
    p = params.require(:user).permit(:sales_orders_show_margin_min)
    @user.update!(p)
    redirect_to user_sales_orders_path
  end

  private
    # Use callbacks to share common setup or constraints between actions.

    # Never trust parameters from the scary internet, only allow the white list through.
    def user_params
      params.require(:user).permit(:name, :remove_occuped_places, :key_user_id, :api_key, :min_pcent_for_advice,
                                   :watch_my_prices, :min_amount_for_advice, :batch_cap, :vol_month_pcent,
          :batch_cap_multiplier )
    end

end
