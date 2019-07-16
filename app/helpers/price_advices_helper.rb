module PriceAdvicesHelper

  def tooltip_price( margin_type )
    return t( 'price_advices.advice_prices.tooltip.price' ) if margin_type == :daily
    t( 'price_advices.advice_prices_monthly.tooltip.price' )
  end

  def trade_hubs_or_regions( margin_type )
    return @trade_hubs_names if margin_type == :daily
    @regions_names
  end

  def trade_hub_name_with_region( trade_hub )
    name = trade_hub.name.clone
    name << ' (' + trade_hub.region.name + ')' if trade_hub.region
    name
  end

  def trade_hub_name_with_region_v2( row_data )
    "#{row_data['trade_hubs.name']} (#{row_data['regions.name']})"
  end

  def price_n_margin( margin_type, item )
    margin_type == :daily ? [ item.min_price, item.margin_comp_immediate ] : [ item.price_avg_week, item.margin_comp_weekly ]
  end

  def challenged_prices_highlight_class_low_margin( margin )
    return 'table-danger' if margin && margin <= 0
    'table-warning' if margin && margin < 0.2
  end

  def challenged_prices_highlight_class_my_price_to_min_price_delta( delta )
    return 'table-danger' if delta && delta < -20
    'table-warning' if delta && delta < 0
  end

  def print_pcent(pcent)
    protected_print_routine( pcent, :pcent )
  end

  def print_pcent_nomultiply(pcent)
    protected_print_routine( pcent, :pcent_nomultiply )
  end

  def print_isk(amount, million_round: false )
    # To ease computation we set the cost to Infinity when we don't have the cost of one of the components
    # But we don't want to show that artifice to the user.
    amount = nil if amount == Float::INFINITY
    protected_print_routine( amount, :isk, million_round: million_round )
  end

  def print_volume(amount)
    protected_print_routine( amount, :volume )
  end

  private

  def protected_print_routine( amount, kind, million_round: nil )
    raise "#{self.class}##{__method__} : amount should not be String" if amount.class == String
    amount ? print_routine( amount, kind, million_round: million_round ) : 'N/A'
  end

  def print_routine( amount, kind, million_round: nil )
    case kind
      when :volume
        number_with_delimiter(amount, separator: ",", delimiter: " ",)
      when :isk
        amount /= 1000000.0 if million_round
        unit = million_round ? 'M ISK ' : 'ISK '

        number_to_currency(amount.round(2), unit: unit, separator: ",", delimiter: " ", format: '%n %u')
      when :pcent, :pcent_nomultiply
        amount = amount * 100.0 if kind == :pcent
        number_with_delimiter(amount.round( 2 ), separator: ",", delimiter: " ",) + ' %'
      else
    end
  end

end
