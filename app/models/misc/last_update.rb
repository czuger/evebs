module Misc
  class LastUpdate < ApplicationRecord

    def self.set( update_type )
      lu = LastUpdate.where( update_type: update_type ).first_or_initialize
      lu.updated_at = Time.now
      lu.save!
    end

  end
end