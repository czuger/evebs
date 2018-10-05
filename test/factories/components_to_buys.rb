FactoryBot.define do
  factory :components_to_buy do
    user { nil }
    eve_item { nil }
    quantity { 1 }
    volume { 1.5 }
  end
end
