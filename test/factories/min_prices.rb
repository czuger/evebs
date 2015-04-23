FactoryGirl.define do
  factory :min_price, :class => 'MinPrice' do
    eve_item nil
    trade_hub nil
    min_price 1.5
  end

end
