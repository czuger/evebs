FactoryBot.define do
  factory :sale_order do
    day {'2018-06-11'}
    cpp_system_id {1}
    cpp_type_id {1}
    price {1.5}
  end
end
