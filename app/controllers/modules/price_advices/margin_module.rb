module Modules::PriceAdvices::MarginModule

  def advice_prices_margins( margin_type )

    raise "#{self.class}##{__method__} : margin_type can't be nil" unless margin_type

    @user = current_user
    set_checked_production_list_ids

    margin_column_name = ( margin_type == :daily ? :margin_comp_immediate : :margin_comp_weekly )

    # caution : use coalesce before vol_month because least forget null value
    # give you full_batch_size instead of zero in case of no sold in month
    # Or add where vol_month is not null
    # Fixed because we filter on vol_month IS NOT NULL

    @items = PriceAdviceMarginComp.where( 'user_id = ?', @user.id )
      .where.not( margin_column_name => nil )

    @items = @items.where( "#{margin_column_name} > min_amount_for_advice" ) if @user.min_amount_for_advice
    @items = @items.where( 'margin_percent > min_pcent_for_advice' ) if @user.min_pcent_for_advice

    if @user.remove_occuped_places
      @items = @items.where.not( @user.user_sale_orders
          .where( 'price_advice_margin_comps.item_id = user_sale_orders.eve_item_id AND price_advice_margin_comps.trade_hub_id = user_sale_orders.trade_hub_id' ).
          exists )
    end

    @items = @items.order( margin_column_name.to_s + ' DESC' )

    @items = @items.paginate(:page => params[:page], :per_page => 20 )

  end
end