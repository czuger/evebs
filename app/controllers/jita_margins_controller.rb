class JitaMarginsController < ApplicationController

  def index
    @margins = JitaMargin.joins(:eve_item).where.not('eve_items.epic_blueprint' => true).paginate(:page => params[:page], per_page: 20).order( 'margin_percent DESC' )
  end

  def update
    eve_item = EveItem.find( params[:id])
    eve_item.update_attribute(:epic_blueprint,true)
    redirect_to jita_margins_path
  end
end
