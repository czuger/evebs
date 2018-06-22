class ComponentsController < ApplicationController
  def show
    @components = Component.joins( :eve_item ).paginate( :page => params[:page], :per_page => 15 )
  end
end
