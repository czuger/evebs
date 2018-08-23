FactoryBot.define do
  factory :crest_cost do
    factory :crest_cost_for_inferno_fury_cruise_missile do
      cpp_item_id {2621}
      eve_item {inferno_fury_cruise_missile}
      adjusted_price {1.5}
      average_price {1.5}
      cost {1.5}
    end
  end
end
