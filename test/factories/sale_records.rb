FactoryGirl.define do
  factory :sale_record do

    user
    eve_client
    eve_item { create( :inferno_fury_cruise_missile ) }
    station

    eve_transaction_key "MyString"

    quantity 1

    unit_sale_price 1.5
    total_sale_price 1.5

    unit_cost 1

    unit_sale_profit 1.5
    total_sale_profit 1.5

    transaction_date_time Time.now

  end

end
