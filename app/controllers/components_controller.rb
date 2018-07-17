class ComponentsController < ApplicationController

  def index
    if params['filter']
      @components = BlueprintComponent.where( "lower( name ) like '%#{params['filter'].downcase}%'" )
                        .order( 'name' ).paginate(:page => params[:page], :per_page => 20 )
    else
      @components = BlueprintComponent.none.paginate(:page => params[:page], :per_page => 20 )
    end

    @filter = params['filter']
  end

  def show
    @component = BlueprintComponent.find( params[ :id ])
    @min_prices = BpcPricesMin.includes( { trade_hub: :region } ).where( blueprint_component_id: @component.id ).order( 'price' )

    @crafted_component = EveItem.find_by_cpp_eve_item_id( @component.cpp_eve_item_id )
  end

  def trade_hub_detail
    @trade_hub = TradeHub.find( params[ :trade_hub_id ] )
    @element = BlueprintComponent.find( params[ :component_id ] )
    @orders = BlueprintComponentSalesOrder.where( trade_hub_id: params[ :trade_hub_id ],
      blueprint_component_id: params[ :component_id ] ).order( 'price' ).limit( 20 )
  end

end
