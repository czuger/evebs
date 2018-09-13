module Esi::Errors
  class OpenTimeout < Base

    def pause
      sleep 60
    end

    def retry?
      true
    end

  end
end