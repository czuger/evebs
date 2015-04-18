class EveItem < ActiveRecord::Base
  has_and_belongs_to_many :users
  has_one :blueprint
  has_many :materials, through: :blueprint
  has_many :components, through: :materials

  def compute_cost
    total_cost = 0
    materials.each do |material|
      if material.component.cost
        total_cost += material.component.cost * material.required_qtt
      else
        puts "Warning !!! #{material.component.inspect} has no cost"
        # If we lack a material we set the price to nil and exit
        update_attribute(:cost,nil)
        return
      end
    end
    update_attribute(:cost,total_cost)
  end

end
