require 'open-uri'
require 'json'

class Fuzzwork::Blueprints

  def update
    EveItem.pluck(:cpp_eve_item_id).each do |id|

      url = "https://www.fuzzwork.co.uk/blueprint/api/blueprint.php?typeid=#{id}"

      r = JSON.parse(open( url ).read)

      if r['blueprintDetails'] && r['activityMaterials'] && r['activityMaterials'].is_a?( Hash )
        pp r['blueprintDetails']
        pp r['activityMaterials']['1']
        p
      end
    end
  end

end