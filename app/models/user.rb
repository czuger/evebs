class User < ActiveRecord::Base
  has_and_belongs_to_many :eve_items
  has_and_belongs_to_many :trade_hubs

  has_many :blueprints, through: :eve_items
  has_many :materials, through: :blueprints
  has_many :components, through: :materials

  def self.get_used_items_and_trade_hubs
    used_item = []
    used_trade_hubs = []
    User.all.to_a.each do |user|
      user.eve_items.each do |eve_item|
        used_item << eve_item unless used_item.include?( eve_item )
      end
      user.trade_hubs.each do |trade_hub|
        used_trade_hubs << trade_hub unless used_trade_hubs.include?( trade_hub )
      end
    end
    [used_item, used_trade_hubs]
  end

end
