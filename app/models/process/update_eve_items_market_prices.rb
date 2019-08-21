module Process

  class UpdateEveItemsMarketPrices

    def update
      Misc::Banner.p 'About to update items market prices'

      cpp_market_prices = YAML::load_file('data/cpp_market_prices.yaml')

      EveItem.transaction do
        EveItem.all.each do |item|
          mp_data = cpp_market_prices[item.cpp_eve_item_id]
          if mp_data
            item.cpp_market_adjusted_price = mp_data['adjusted_price']
            item.cpp_market_average_price = mp_data['average_price']
          end

          item.save!
        end
      end

      Misc::Banner.p 'Update items finished'
    end
  end

end

