FactoryGirl.define do
  sequence :cpp_eve_item_id do |n|
    n
  end
  sequence :name do |n|
    "Item id #{n}"
  end
  factory :eve_item do
    cpp_eve_item_id
    name
  end
end
