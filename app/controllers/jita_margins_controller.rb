class JitaMarginsController < ApplicationController

  before_action :log_client_activity
  before_action :require_logged_in!, except: [ :index ]

  def index
    # TODO : download prod database and try localy
    @margins = JitaMargin.joins(:eve_item).includes( :eve_item ).where.not('eve_items.epic_blueprint' => true)
      .where( 'margin_percent > 0.4' ).where( 'mens_volume > 0' )
      .order( 'margin DESC' ).limit( 5 )
  end

  def update
    eve_item = EveItem.find( params[:id] )
    eve_item.update_attribute(:epic_blueprint,true)
    redirect_to jita_margins_path
  end
end
