module PriceAdvicesHelper

	AMOUNTS = { billion: { amount: 10.0 ** 9, unit: 'B'.freeze },
							million: { amount: 10.0 ** 6, unit: 'M'.freeze },
							kilo: { amount: 10.0 ** 3, unit: 'K'.freeze } }

	ORDERED_AMOUNTS = [ :billion, :million, :kilo ]

  def margin_detail_tooltip( item, price, margin, margin_type )
		result = "<p>Single unit cost : <br>#{print_isk( item.single_unit_cost )}</p>"

		price_lib = ( margin_type == :daily ? 'Current min price' : 'Weekly average min price' )
		result << "<p>#{price_lib} : <br>#{print_isk( price )}</p>"

		result << "<p>Single item margin : <br>#{print_isk( price - item.single_unit_cost )}</p>"

		result << "<p>Target volume (#{@user.vol_month_pcent}%) : <br>#{print_volume( item.vol_month * @user.vol_month_pcent * 0.01 )}</p>"

		result
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

  def print_isk(amount, million_round: true )
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
        # number_with_delimiter(amount, separator: ",", delimiter: " ",)

				to_small_number( amount )
      when :isk
        unit = ''

        # if million_round && amount >= 1000000
        #   amount /= 1000000.0
        #   unit = 'M'
        # end

        # number_to_currency(amount.round(2), unit: unit, separator: ",", delimiter: " ", format: '%n %u')

				to_small_number( amount )
      when :pcent, :pcent_nomultiply
        amount = amount * 100.0 if kind == :pcent
        number_with_delimiter(amount.round( 2 ), separator: ",", delimiter: " ",) + ' %'
      else
    end
	end

	def to_small_number( amount )
		ORDERED_AMOUNTS.each do |oa_key|
			if amount >= AMOUNTS[oa_key][:amount]
				new_amount = amount / AMOUNTS[oa_key][:amount]
				return format_small_number( new_amount ) + AMOUNTS[oa_key][:unit]
			end
		end

		format_small_number amount
	end

	def format_small_number( new_amount )
		print_format =
			case new_amount
				when 0..9
					'%1.2f'
				when 10..99
					'%2.1f'
				else
					'%3.0f'
			end

		return ( print_format % new_amount )
	end

	# TODO : sur mobile, afficher la taille du breadcrumb en fonction du nombre de caractères du dernier élément.
	# Utiliser un partial avec une variable locale

end
