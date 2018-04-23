FactoryBot.define do
  factory :eve_market_history_error do
    cpp_region_id 1
    cpp_eve_item_id 1
    error "MyString"
  end
end
