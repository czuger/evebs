module PriceAdvicesHelper
  def print_isk(amount)
    if amount
      number_to_currency(amount.round(1), unit: "ISK ", separator: ",", delimiter: " ", format: '%n %u')
    end
  end
end
