class ComponentsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def show
    @component = BlueprintComponent.find( params[ :id ])
    @min_prices = BlueprintComponentSalesOrder.where( blueprint_component_id: @component.id )
      .group( :trade_hub_id ).minimum( :price )

    @trade_hubs_hash = Hash[ TradeHub.all.map { |t| [ t.id, t ] } ]
  end
end
