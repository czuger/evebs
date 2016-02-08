class JitaMarginsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def index
    @margins = JitaMargin.joins(:eve_item).includes( :eve_item ).where.not('eve_items.epic_blueprint' => true).order( 'margin DESC' ).limit( 10 )
  end

  def update
    eve_item = EveItem.find( params[:id] )
    eve_item.update_attribute(:epic_blueprint,true)
    redirect_to jita_margins_path
  end
end
