FactoryGirl.define do
  factory :user do
    name "MyString"
    remove_occuped_places true
    key_user_id "MyString"
    api_key "MyString"
    min_pcent_for_advice 10
    min_amount_for_advice 10000000

    after(:create) do |user|
      item = create( :inferno_fury_cruise_missile )
      user.eve_items << item
    end

  end

end
