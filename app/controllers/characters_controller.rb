class CharactersController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_character, only: [:edit, :update]

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

  private

  def set_character
    @character = Character.find( params[:id] )
  end

  # Never trust parameters from the scary internet, only allow the white list through.
  def character_params
    params.require(:character).permit( :download_my_assets, :locked )
  end

end
