class User < ActiveRecord::Base

  has_and_belongs_to_many :eve_items
  has_and_belongs_to_many :trade_hubs

  has_many :blueprints, through: :eve_items
  has_many :materials, through: :blueprints
  has_many :components, through: :materials
  has_many :trade_orders

  def self.from_omniauth(auth)
    if auth["provider"] == 'identity'
      find_by_provider_and_uid(auth['provider'], auth['uid']) || create_with_omniauth(auth)
    else
      where(provider: auth["provider"], uid: auth["uid"]).first_or_initialize.tap do |user|
        user.provider = auth.provider
        user.uid = auth.uid
        user.name = auth.info.name
        user.oauth_token = auth.credentials.token
        user.oauth_expires_at = Time.at(auth.credentials.expires_at)
        user.save!
      end
    end
  end

  def self.create_with_omniauth(auth)
    create! do |user|
      user.provider = auth['provider']
      user.uid = auth['uid']
      user.name = auth['info']['name']
    end
  end


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

  def get_occuped_places
    trade_orders.map{ |to| [to.trade_hub.id,to.eve_item_id] }
  end

end
