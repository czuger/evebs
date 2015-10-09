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
        number_to_currency(amount.round(1), unit: "ISK ", separator: ",", delimiter: " ", format: '%n %u')
      when :pcent
        "#{amount} %"
      else

    end
  end

end
