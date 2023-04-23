
#the libraries

import pefile
import hashlib
import os

def func(file_path):
    pe = pefile.PE(file_path)
    column_names = ['Name', 'md5', 'Machine', 'SizeOfOptionalHeader', 'Characteristics',
                    'MajorLinkerVersion', 'MinorLinkerVersion', 'SizeOfCode',
                    'SizeOfInitializedData', 'SizeOfUninitializedData',
                    'AddressOfEntryPoint', 'BaseOfCode', 'BaseOfData', 'ImageBase',
                    'SectionAlignment', 'FileAlignment', 'MajorOperatingSystemVersion',
                    'MinorOperatingSystemVersion', 'MajorImageVersion', 'MinorImageVersion',
                    'MajorSubsystemVersion', 'MinorSubsystemVersion', 'SizeOfImage',
                    'SizeOfHeaders', 'CheckSum', 'Subsystem', 'DllCharacteristics',
                    'SizeOfStackReserve', 'SizeOfStackCommit', 'SizeOfHeapReserve',
                    'SizeOfHeapCommit', 'LoaderFlags', 'NumberOfRvaAndSizes', 'SectionsNb',
                    'SectionsMeanEntropy', 'SectionsMinEntropy', 'SectionsMaxEntropy',
                    'SectionsMeanRawsize', 'SectionsMinRawsize', 'SectionMaxRawsize',
                    'SectionsMeanVirtualsize', 'SectionsMinVirtualsize',
                    'SectionMaxVirtualsize', 'ImportsNbDLL', 'ImportsNb',
                    'ImportsNbOrdinal', 'ExportNb', 'ResourcesNb', 'ResourcesMeanEntropy',
                    'ResourcesMinEntropy', 'ResourcesMaxEntropy', 'ResourcesMeanSize',
                    'ResourcesMinSize', 'ResourcesMaxSize', 'LoadConfigurationSize',
                    'VersionInformationSize']



    # Initialize an empty dictionary to store the extracted data

    pe_data = {}

    # Loop over the column names and extract their respective data from the PE file
    for column in column_names:
        try:
            #for finding the name
            if column == 'Name':
                pe_data[column] = os.path.basename(file_path)
                # pe_data[column] = pe.FILE_HEADER.FileName.decode('utf-8', 'ignore')
                
            #for finding the md5 value
            elif column == 'md5':
                with open(file_path, "rb") as f:
                    md5 = hashlib.md5(f.read()).hexdigest()
                pe_data[column] = md5
            else:
                try:
                    pe_data[column] = pe.OPTIONAL_HEADER.__getattribute__(column)
                except AttributeError:
                    pe_data[column] = pe.FILE_HEADER.__getattribute__(column)
            
                
        except AttributeError:
            pe_data[column] = 0

    data_dict = {
        
        'SectionsNb': pe.FILE_HEADER.NumberOfSections,
        'SectionsMeanEntropy': pe.sections[-1].get_entropy(),
        'SectionsMinEntropy': min(section.get_entropy() for section in pe.sections),
        'SectionsMaxEntropy': max(section.get_entropy() for section in pe.sections),
        'SectionsMeanRawsize': sum(section.SizeOfRawData for section in pe.sections) / len(pe.sections),
        'SectionsMinRawsize': min(section.SizeOfRawData for section in pe.sections),
        'SectionMaxRawsize': max(section.SizeOfRawData for section in pe.sections),
        'SectionsMeanVirtualsize': sum(section.Misc_VirtualSize for section in pe.sections) / len(pe.sections),
        'SectionsMinVirtualsize': min(section.Misc_VirtualSize for section in pe.sections),
        'SectionMaxVirtualsize': max(section.Misc_VirtualSize for section in pe.sections),
        'ImportsNbDLL': len(pe.DIRECTORY_ENTRY_IMPORT),
        'ImportsNb': sum(len(x.imports) for x in pe.DIRECTORY_ENTRY_IMPORT),
        'ImportsNbOrdinal': sum(1 for x in pe.DIRECTORY_ENTRY_IMPORT for i in x.imports if i.import_by_ordinal is not None),
        # 'ExportNb': len(pe.DIRECTORY_ENTRY_EXPORT.symbols),
        # 'ResourcesNb': len(pe.DIRECTORY_ENTRY_RESOURCE.entries),
        # 'ResourcesMeanEntropy': sum(entry.get_entropy() for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries) / len(pe.DIRECTORY_ENTRY_RESOURCE.entries),
        # 'ResourcesMinEntropy': min(entry.get_entropy() for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries),
        # 'ResourcesMaxEntropy': max(entry.get_entropy() for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries),
        # 'ResourcesMeanSize': sum(entry.SizeOfData for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries) / len(pe.DIRECTORY_ENTRY_RESOURCE.entries),
        # 'ResourcesMinSize': min(entry.SizeOfData for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries),
        # 'ResourcesMaxSize': max(entry.SizeOfData for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries),
        'LoadConfigurationSize': pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG']].Size,
        # 'VersionInformationSize': pe.VS_FIXEDFILEINFO.StructureSize
    }
    # pe.close()
        
    return pe_data