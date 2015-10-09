FactoryGirl.define do
  factory :user do

    name "MyString"
    remove_occuped_places true
    key_user_id "MyString"
    api_key "MyString"
    min_pcent_for_advice 10
    min_amount_for_advice 10000000

    transient do
      region nil
    end

    after(:create) do |user, evaluator|
      user.eve_items = EveItem.all
      user.trade_hubs = evaluator.region.trade_hubs if evaluator.region
    end

  end
end
