class Component < ActiveRecord::Base
  JITA_EVE_SYSTEM_ID=30000142

  validates :cpp_eve_item_id, :name, presence: true
  include MinPriceRetriever

  has_many :materials
  has_many :blueprints, through: :materials
  has_many :eve_items, through: :blueprints
  has_many :users, through: :eve_items

  def set_min_price
    min_price = get_min_price_from_eve_central(cpp_eve_item_id,JITA_EVE_SYSTEM_ID)
    if min_price
      update_attribute( :cost, min_price )
    end
  end

end
