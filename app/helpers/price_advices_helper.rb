module PriceAdvicesHelper
  def print_isk(amount)
    if amount
      if amount.class != String
        number_to_currency(amount.round(1), unit: "ISK ", separator: ",", delimiter: " ", format: '%n %u')
      else
        amount
      end
    end
  end
end
