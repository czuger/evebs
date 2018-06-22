class ComponentsController < ApplicationController
  def show
    @components = Component.joins( :eve_item ).order( 'blueprints_count DESC NULLS LAST' ).paginate( :page => params[:page], :per_page => 15 )
  end
end
