module PriceAdvicesHelper

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
