module ItemsHelper

  def print_total_cost_for_items( item )
    single_cost = item.prices_advices.first
    return 'N/A' unless single_cost
    "( #{print_isk( single_cost.single_unit_cost )})"
  end

  def tooltip_price( margin_type )
    return t( 'price_advices.advice_prices.tooltip.price' ) if margin_type == :daily
    t( 'price_advices.advice_prices_monthly.tooltip.price' )
  end

  def trade_hubs_or_regions( margin_type )
    return @trade_hubs_names if margin_type == :daily
    @regions_names
  end

  def trade_hub_name_with_region( trade_hub )
    name = trade_hub.name
    name << ' (' + trade_hub.region.name + ')' if trade_hub.region
    name
  end

  def price_n_margin( margin_type, item )
    price = margin_type == :daily ? item.min_price : item.avg_price

    if @batch_cap
      batch = [ item.full_batch_size, item.vol_month * @vol_month_pcent ].min
    else
      batch = item.vol_month * @vol_month_pcent
    end

    margin = ( batch * price ) - ( batch * item.single_unit_cost )
    margin_pcent = (( batch * price ) / ( batch * item.single_unit_cost )) -1
    [ price, batch.floor, margin, margin_pcent ]
  end

  def eve_central_quicklook_link( margin_type, price, item )
    # if margin_type == :daily
    #   return link_to( print_isk(price), "https://eve-central.com/home/quicklook.html?typeid=#{item.eve_item.cpp_eve_item_id}&usesystem=#{item.trade_hub.eve_system_id}", target: '_blank' )
    # end
    print_isk(price)
  end

  def shopping_basket_check_box( item )
    id = [ @user.id, item[:trade_hub_id], item[:eve_item_id] ]
    check_box_tag(
      "eve_item_#{id.join('_')}", id.join( '|' ),
      @shopping_basket.include?( [ @user.id, item[:trade_hub_id], item[:eve_item_id ] ] ),
      { class: :shopping_basket_checkbox }
    )
  end

  def challenged_prices_highlight_class_low_margin( margin )
    return :danger if margin && margin <= 0
    :warning if margin && margin < 0.2
  end

  def challenged_prices_highlight_class_my_price_to_min_price_delta( delta )
    return :danger if delta && delta < -20
    :warning if delta && delta < 0
  end

  def cell_classes( region_printed, cell_position, cell_align, row_class, last_row )
    classes_array = []
    if cell_position == :left
      classes_array << :boxed_cell_left_start
    else
      classes_array << "cell_#{cell_align}_align"
    end

    classes_array << :boxed_cell_middle_left_border if cell_position == :middle_middle

    unless region_printed
      classes_array << :boxed_cell_middle_start
    end

    classes_array << :boxed_cell_middle_end if last_row

    classes_array << row_class

    classes_array
  end

  def print_pcent(pcent)
    protected_print_routine( pcent, :pcent )
  end

  def print_isk(amount)
    protected_print_routine( amount, :isk )
  end

  def print_volume(amount)
    protected_print_routine( amount, :volume )
  end

  private

  def protected_print_routine( amount, kind )
    raise "#{self.class}##{__method__} : amount should not be String" if amount.class == String
    amount ? print_routine( amount, kind ) : 'N/A'
  end

  def print_routine( amount, kind )
    case kind
      when :volume
        number_with_delimiter(amount, separator: ",", delimiter: " ",)
      when :isk
        number_to_currency(amount.round(2), unit: "ISK ", separator: ",", delimiter: " ", format: '%n %u')
      when :pcent
        number_with_delimiter((amount * 100).round( 2 ), separator: ",", delimiter: " ",) + ' %'
      else
    end
  end

end
