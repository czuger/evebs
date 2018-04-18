require 'test_helper'

class ComputePriceHistoryAvgTest < ActiveSupport::TestCase

  test "Should create one item in crest_prices_last_month_averages" do
    create( :crest_price_history, history_date: Time.now, day_timestamp: '' )
    assert_difference 'CrestPricesLastMonthAverage.count' do
      Crest::ComputePriceHistoryAvg.new
    end
  end

  test "Should not create one item in crest_prices_last_month_averages" do
    create( :crest_price_history, history_date: Time.now, day_timestamp: '' )
    Crest::ComputePriceHistoryAvg.new
    assert_no_difference 'CrestPricesLastMonthAverage.count' do
      Crest::ComputePriceHistoryAvg.new
    end
  end

end
