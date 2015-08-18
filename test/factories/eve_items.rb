FactoryGirl.define do
  sequence :cpp_eve_item_id do |n|
    n
  end
  sequence :name do |n|
    "Item id #{n}"
  end
  sequence :name_lowcase do |n|
    "item id #{n}"
  end
  factory :eve_item do
    cpp_eve_item_id 5
    name
    name_lowcase
    cost 5
  end
end
