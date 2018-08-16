class UserToUserDuplicationRequestsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [ :index, :new, :create ]
  before_action :set_user_to_user_duplication_request, only: [ :destroy ]

  # GET /user_to_user_duplication_requests
  # GET /user_to_user_duplication_requests.json
  def index
    @user_to_user_duplication_requests_as_sender = @user.user_to_user_duplication_requests_as_senders.all
    @user_to_user_duplication_requests_as_reciever = @user.user_to_user_duplication_requests_as_receivers.all
  end

  # GET /user_to_user_duplication_requests/1
  # GET /user_to_user_duplication_requests/1.json
  def show
  end

  # GET /user_to_user_duplication_requests/new
  def new
    @user_to_user_duplication_request = UserToUserDuplicationRequest.new

    @available_users = User.where.not( id: @user.id ).pluck( :name, :id )
  end

  # POST /user_to_user_duplication_requests
  # POST /user_to_user_duplication_requests.json
  def create
    @user_to_user_duplication_request = UserToUserDuplicationRequest.new(user_to_user_duplication_request_params)
    @user_to_user_duplication_request.sender_id = @user.id

    respond_to do |format|
      if @user_to_user_duplication_request.save
        format.html { redirect_to @user_to_user_duplication_request, notice: 'User to user duplication request was successfully created.' }
      else
        format.html { render :new }
      end
    end
  end

  # DELETE /user_to_user_duplication_requests/1
  # DELETE /user_to_user_duplication_requests/1.json
  def destroy
    @user_to_user_duplication_request.destroy
    respond_to do |format|
      format.html { redirect_to user_to_user_duplication_requests_url, notice: 'User to user duplication request was successfully destroyed.' }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_user_to_user_duplication_request
      @user_to_user_duplication_request = UserToUserDuplicationRequest.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def user_to_user_duplication_request_params
      params.require(:user_to_user_duplication_request).permit(:receiver_id, :duplication_type)
    end
end