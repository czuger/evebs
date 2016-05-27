module PriceAdvicesHelper

  def tooltip_price( margin_type )
    return t( 'price_advices.advice_prices.tooltip.price' ) if margin_type == :daily
    t( 'price_advices.advice_prices_monthly.tooltip.price' )
  end

  def trade_hubs_or_regions( margin_type )
    return @trade_hubs_names if margin_type == :daily
    @regions_names
  end

  def eve_central_quicklook_link( margin_type, item )
    if margin_type == :daily
      return link_to( print_isk(item[:price]), "https://eve-central.com/home/quicklook.html?typeid=#{item[:cpp_eve_item_id]}&usesystem=#{item[:cpp_system_id]}", target: '_blank' )
    end
    print_isk(item[:price])
  end

  def shopping_basket_check_box( item )
    id = [ @user.id, item[:trade_hub_id], item[:eve_item_id] ]
    check_box_tag(
      "eve_item_#{id.join('_')}", id.join( '|' ),
      @shopping_basket.include?( [ @user.id, item[:trade_hub_id], item[:eve_item_id ] ] ),
      { class: :shopping_basket_checkbox }
    )
  end

  def shopping_basket_check_box_shopping_basket( basket )
    id = [ @user.id, basket.trade_hub_id, basket.eve_item_id ]
    check_box_tag(
      "eve_item_#{id.join('_')}", id.join( '|' ), true,
      { class: [:shopping_basket_checkbox, :delete_on_change], 'data-toggle' => :tooltip, title: 'Uncheck to remove item' }
    )
  end

  def challenged_prices_highlight_class_low_margin( margin )
    return :danger if margin && margin <= 0
    :warning if margin && margin < 0.2
  end

  def challenged_prices_highlight_class_my_price_to_min_price_delta( delta )
    puts delta
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
