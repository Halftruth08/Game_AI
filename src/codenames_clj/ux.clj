(ns codenames_clj.ux
 (:require [clojure.java.io :as io]
           [clojure.string :as string]
           [seesaw.core :as ssw]
           [seesaw.color :as color]
           )
  )

(defn popopen
  ""
  [title content]
  (let [fr (ssw/frame :title title, :content content, :on-close :exception)]
    (-> fr
        ssw/pack!
        ssw/show!))
   )

(def window1 (ssw/frame :title "Unchanged", :content (ssw/grid-panel
                                                       :border "Codenames"
                                                       :columns 5
                                                       :items (repeat 25 "nil"))))


(defn window
  ""
  [title content]
  (ssw/frame :title title, :content content, :on-close :exception))

(defn update_config
  [fr kw newcontent]
  (ssw/config! fr kw newcontent))


(defn show
  ""
  [fr]
  (-> fr
      ssw/pack!
      ssw/show!))

(defn lbl
  ""
  [stri]
  (ssw/label stri))

()

(defn buttons
  ""
  [words]
  (def bvec (map #(ssw/button :text %,
                              :font "ARIAL-BOLD-18",
                              ;:selected-text-color (color/color 255 255 0)
                              :listen [:action (fn [event] (ssw/alert %))]) words))
  (ssw/grid-panel
    :columns 5
    :items bvec))