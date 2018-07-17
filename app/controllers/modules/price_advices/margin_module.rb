module Modules::PriceAdvices::MarginModule

  def advice_prices_margins( margin_type )

    raise "#{self.class}##{__method__} : margin_type can't be nil" unless margin_type

    @user = current_user
    # @prices_array = []
    # @monthly_averages = get_montly_items_averages

    @checked_production_list_ids = @user.production_lists.joins(
        'INNER JOIN prices_advices ON production_lists.trade_hub_id = prices_advices.trade_hub_id AND production_lists.eve_item_id = prices_advices.eve_item_id' )
      .pluck( 'prices_advices.id' )

    # TODO : those variables need to be in the user
    # Monthly volume percent multiplier for margin computation (default 10 %)
    @vol_month_pcent = @user.vol_month_pcent * 0.01
    # Monthly volume capped by full batch ?
    @batch_cap = @user.batch_cap

    price_column_name = margin_type == :daily ? :min_price : :avg_price

    # TODO : caution : use coalesce before vol_month because least forget null value
    # give you full_batch_size instead of zero in case of no sold in month
    # Or add where vol_month is not null
    if @batch_cap
      batch_size_formula = "LEAST( full_batch_size, FLOOR( vol_month * #{@vol_month_pcent} ) )"
    else
      batch_size_formula = "FLOOR( vol_month * #{@vol_month_pcent} )"
    end

    @items = PricesAdvice.includes( :eve_item, :region ).where( eve_item: @user.eve_items, trade_hub: @user.trade_hubs )
    .where.not( vol_month: nil )

    if margin_type == :daily
      @items = @items.includes( :trade_hub )
    end

    if @user.min_amount_for_advice
      margin_comp = "((#{price_column_name}*#{batch_size_formula}) - (single_unit_cost*#{batch_size_formula}))"
      @items = @items.where( "#{margin_comp} > #{@user.min_amount_for_advice}" )
    end

    @items = @items.where( 'margin_percent > ?', @user.min_pcent_for_advice ) if @user.min_pcent_for_advice

    if @user.remove_occuped_places
      @items = @items.where.not( @user.trade_orders
          .where( 'prices_advices.eve_item_id = trade_orders.eve_item_id AND prices_advices.trade_hub_id = trade_orders.trade_hub_id' ).
          exists )
    end

    @items = @items.order( margin_comp + ' DESC' ) if margin_comp

    @items = @items.paginate(:page => params[:page], :per_page => 15 )

  end
end