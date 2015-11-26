class UsersController < ApplicationController

  before_action :set_user, only: [:show, :edit, :update, :destroy]

  before_action :require_logged_in!, except: [ :helps ]

  before_action :log_client_activity

  # GET /users/1/edit
  def edit
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
          format.html { render :edit, notice: 'User was successfully updated.' }
        else
          format.html { render :edit }
        end
      end
    end
  end

  def edit_password
  end

  def change_password
    @user = current_user
    @identity = Identity.find( @user.uid )
    @identity.password = params['new_password']
    @identity.password_confirmation = params['new_password_confirmation']
    result = @identity.save
    unless result
      flash[:errors] = @identity.errors
    else
      flash[:success] = true
    end

    redirect_to  user_edit_password_path
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_user
      @user = current_user
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def user_params
      params.require(:user).permit(:name, :remove_occuped_places, :key_user_id, :api_key, :min_pcent_for_advice,
                                   :watch_my_prices, :min_amount_for_advice)
    end

end
