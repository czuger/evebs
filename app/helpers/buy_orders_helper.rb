module BuyOrdersHelper

  def buy_orders_margin_detail_tooltip( line_data, final_margin )
    result = "<p>Single unit cost : <br>#{print_isk( line_data.single_unit_cost )}</p>"

    result << "<p>Approx buy price : <br>#{print_isk( line_data.approx_max_price )}</p>"

    result << "<p>Single item margin : <br>#{print_isk( line_data.single_unit_margin )}</p>"

		if @user.batch_cap
			result << "<p>Batch cap enabled"
			result << "<br>Batch cap : #{print_volume(line_data.batch_cap)}</p>"
		end

		volume = @user.batch_cap ? line_data.capped_volume : line_data.over_approx_max_price_volume
    result << "<p>Buy volume : <br>#{print_volume(volume)}</p>"

		result << '<p>Margin'
		result << "<br>#{print_volume(volume)} * #{print_isk( line_data.single_unit_margin )}"
		result << "<br>= #{print_isk( final_margin )}"

    result
  end
end
