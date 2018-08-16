class UserToUserDuplicationRequestsController < ApplicationController
  before_action :set_user_to_user_duplication_request, only: [:show, :edit, :update, :destroy]

  # GET /user_to_user_duplication_requests
  # GET /user_to_user_duplication_requests.json
  def index
    @user_to_user_duplication_requests = UserToUserDuplicationRequest.all
  end

  # GET /user_to_user_duplication_requests/1
  # GET /user_to_user_duplication_requests/1.json
  def show
  end

  # GET /user_to_user_duplication_requests/new
  def new
    @user_to_user_duplication_request = UserToUserDuplicationRequest.new
  end

  # GET /user_to_user_duplication_requests/1/edit
  def edit
  end

  # POST /user_to_user_duplication_requests
  # POST /user_to_user_duplication_requests.json
  def create
    @user_to_user_duplication_request = UserToUserDuplicationRequest.new(user_to_user_duplication_request_params)

    respond_to do |format|
      if @user_to_user_duplication_request.save
        format.html { redirect_to @user_to_user_duplication_request, notice: 'User to user duplication request was successfully created.' }
        format.json { render :show, status: :created, location: @user_to_user_duplication_request }
      else
        format.html { render :new }
        format.json { render json: @user_to_user_duplication_request.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /user_to_user_duplication_requests/1
  # PATCH/PUT /user_to_user_duplication_requests/1.json
  def update
    respond_to do |format|
      if @user_to_user_duplication_request.update(user_to_user_duplication_request_params)
        format.html { redirect_to @user_to_user_duplication_request, notice: 'User to user duplication request was successfully updated.' }
        format.json { render :show, status: :ok, location: @user_to_user_duplication_request }
      else
        format.html { render :edit }
        format.json { render json: @user_to_user_duplication_request.errors, status: :unprocessable_entity }
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
      params.require(:user_to_user_duplication_request).permit(:reciever_id, :duplication_type)
    end
end
