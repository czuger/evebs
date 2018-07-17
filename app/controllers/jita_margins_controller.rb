class JitaMarginsController < ApplicationController

  before_action :log_client_activity
  before_action :require_logged_in!, except: [ :index ]

  caches_page :index

  def index
    # @margins = JitaMargin.includes( :eve_item )
    #   .where( 'margin_percent > 0.3' ).where( 'mens_volume > ( batch_size * 600 )' )
    #   .order( 'margin DESC' ).limit( 5 )
  end

  # def update
  #   eve_item = EveItem.find( params[:id] )
  #   eve_item.update_attribute(:epic_blueprint,true)
  #   redirect_to jita_margins_path
  # end
end
