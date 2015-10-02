module PriceAdvicesHelper

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
      { class: [:shopping_basket_checkbox, :delete_on_change] }
    )
  end


  def print_pcent(pcent)
    if pcent
      pcent = (pcent*100).round(1)
      "#{pcent} %"
    else
      'N/A'
    end
  end

  def print_isk(amount)
    if amount
      if amount.class != String
        number_to_currency(amount.round(1), unit: "ISK ", separator: ",", delimiter: " ", format: '%n %u')
      else
        amount
      end
    else
      'N/A'
    end
  end

  def print_volume(amount)
    if amount
      if amount.class != String
        number_with_delimiter(amount, separator: ",", delimiter: " ",)
      else
        amount
      end
    else
      'N/A'
    end
  end

end
