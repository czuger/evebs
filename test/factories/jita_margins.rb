FactoryBot.define do

  factory :jita_margin do
    eve_item { create( :inferno_fury_cruise_missile ) }
    margin {1.5}
  end

end
