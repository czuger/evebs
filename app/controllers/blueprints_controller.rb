class BlueprintsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [:show]

  def edit
    @character = Character.find( params[:id] )
  end

  def update
    respond_to do |format|
      if @character.update(character_params)
        flash.now[ :notice ] = 'Character updated successfully.'
        format.html { render :edit }
      else
        flash.now[ :alert ] = @user.errors
        format.html { render :edit }
      end
    end
  end

end
